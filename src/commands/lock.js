const { SlashCommandBuilder, PermissionFlagsBits, PermissionsBitField } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('lock')
        .setDescription('Kanalı kilitler (mesaj gönderimini kapatır).')
        .setDefaultMemberPermissions(PermissionFlagsBits.ManageChannels),
    async execute(interaction) {
        try {
            await interaction.channel.permissionOverwrites.edit(interaction.guild.id, {
                SendMessages: false
            });
            
            await interaction.reply('🔒 Kanal kilitlendi. Artık mesaj gönderilemez.');
        } catch (error) {
            console.error('Lock error:', error);
            await interaction.reply({ content: '❌ Kanal kilitlenemedi.', ephemeral: true });
        }
    }
};
