const { SlashCommandBuilder, PermissionFlagsBits } = require('discord.js');
const { setBirthdayChannel } = require('../database');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('birthdaychatroom')
        .setDescription('Doğum günü duyurularının yapılacağı kanalı ayarlar.')
        .addChannelOption(option =>
            option.setName('channel')
                .setDescription('Doğum günü kanalı')
                .setRequired(true))
        .setDefaultMemberPermissions(PermissionFlagsBits.Administrator),
    async execute(interaction) {
        const channel = interaction.options.getChannel('channel');

        setBirthdayChannel(interaction.guild.id, channel.id);

        await interaction.reply({
            content: `🎂 Doğum günü duyuruları artık ${channel} kanalında yapılacak!`,
            ephemeral: true
        });
    }
};
