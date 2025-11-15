const { SlashCommandBuilder, PermissionFlagsBits } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('haberrss')
        .setDescription('RSS feed\'lerden güncel haberlerin gönderileceği kanalı ayarlar.')
        .addChannelOption(option =>
            option.setName('kanal')
                .setDescription('Haberlerin gönderileceği kanal')
                .setRequired(true))
        .setDefaultMemberPermissions(PermissionFlagsBits.Administrator),
    async execute(interaction) {
        const channel = interaction.options.getChannel('kanal');

        // TODO: Implement RSS feed storage and periodic updates
        
        await interaction.reply({
            content: `📰 RSS haber özelliği henüz geliştirilme aşamasındadır. Kanal: ${channel}`,
            ephemeral: true
        });
    }
};
